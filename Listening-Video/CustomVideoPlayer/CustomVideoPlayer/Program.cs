using Avalonia;
using System;
using LibVLCSharp.Shared;

namespace CustomVideoPlayer;

class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        // Initialize LibVLC native engine before UI launches
        Core.Initialize();

        BuildAvaloniaApp()
            .StartWithClassicDesktopLifetime(args);
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .WithInterFont()
            .LogToTrace();
}
