using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using QuickLook.Common.Plugin;

namespace QuickLook.Plugin.XisfViewer
{
    // Intentionally keeps the FITS viewer untouched; handles only .xisf.
    public sealed class Plugin : IViewer
    {
        private CancellationTokenSource _cts;
        public int Priority => 0;

        public void Init() { }

        public bool CanHandle(string path) =>
            !Directory.Exists(path) &&
            string.Equals(Path.GetExtension(path), ".xisf", StringComparison.OrdinalIgnoreCase);

        public void Prepare(string path, ContextObject context)
        {
            context.PreferredSize = new Size(1120, 790);
        }

        public void View(string path, ContextObject context)
        {
            var root = new Grid { Background = new SolidColorBrush(Color.FromRgb(19, 22, 29)) };
            root.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            root.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            var image = new Image
            {
                Stretch = Stretch.Uniform,
                HorizontalAlignment = HorizontalAlignment.Stretch,
                VerticalAlignment = VerticalAlignment.Stretch
            };
            RenderOptions.SetBitmapScalingMode(image, BitmapScalingMode.HighQuality);
            Grid.SetRow(image, 0);
            root.Children.Add(image);

            var status = new TextBlock
            {
                Text = "Odczyt XISF i obliczanie AutoSTF...",
                Foreground = Brushes.Gainsboro,
                Background = new SolidColorBrush(Color.FromRgb(33, 38, 47)),
                Padding = new Thickness(12, 8, 12, 8),
                TextWrapping = TextWrapping.Wrap
            };
            Grid.SetRow(status, 1);
            root.Children.Add(status);

            context.ViewerContent = root;
            context.Title = Path.GetFileName(path);
            context.IsBusy = true;

            _cts?.Cancel();
            _cts?.Dispose();
            var tokenSource = _cts = new CancellationTokenSource();
            var token = tokenSource.Token;

            Task.Run(() => XisfDecoder.Preview(path, token), token)
                .ContinueWith(task =>
                {
                    if (token.IsCancellationRequested) return;
                    try
                    {
                        if (task.IsFaulted)
                        {
                            var ex = task.Exception?.GetBaseException();
                            status.Text = "Nie udało się otworzyć XISF: " + (ex?.Message ?? "Nieznany błąd");
                        }
                        else if (task.IsCanceled)
                        {
                            status.Text = "Anulowano odczyt";
                        }
                        else
                        {
                            var preview = task.Result;
                            var bitmap = BitmapSource.Create(preview.Width, preview.Height,
                                96, 96, PixelFormats.Bgr24, null, preview.Bgr,
                                preview.Width * 3);
                            bitmap.Freeze();
                            image.Source = bitmap;
                            status.Text = preview.Info;
                        }
                    }
                    finally { context.IsBusy = false; }
                }, CancellationToken.None, TaskContinuationOptions.None,
                TaskScheduler.FromCurrentSynchronizationContext());
        }

        public void Cleanup()
        {
            _cts?.Cancel();
            _cts?.Dispose();
            _cts = null;
        }
    }
}
