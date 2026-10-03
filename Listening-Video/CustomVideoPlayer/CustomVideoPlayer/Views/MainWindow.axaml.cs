using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Platform.Storage;
using Avalonia.Threading;
using LibVLCSharp.Shared;

namespace CustomVideoPlayer.Views
{
    public class SubtitleItem
    {
        public double Start { get; set; }
        public double End { get; set; }
        public string TextEn { get; set; } = string.Empty;
        public string TextEs { get; set; } = string.Empty;
    }

    public partial class MainWindow : Window
    {
        private LibVLC? _libVlc;
        private MediaPlayer? _mediaPlayer;
        private List<SubtitleItem> _subtitles = new();
        private DispatcherTimer? _loopTimer;

        private long _intervalStartMs = 0;
        private const long IntervalMs = 15000; // 15-second loop window
        private bool _isSecondPass = false;

        public MainWindow()
        {
            InitializeComponent();

            Core.Initialize();

            _libVlc = new LibVLC();
            _mediaPlayer = new MediaPlayer(_libVlc);

            this.Loaded += (s, e) =>
            {
                if (VideoViewer != null)
                {
                    VideoViewer.MediaPlayer = _mediaPlayer;
                }
            };

            _loopTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(100)
            };
            _loopTimer.Tick += OnLoopTimerTick;
            _loopTimer.Start();
        }

        private async void OnOpenVideoClicked(object? sender, RoutedEventArgs e)
        {
            var topLevel = TopLevel.GetTopLevel(this);
            if (topLevel == null || _libVlc == null) return;

            var files = await topLevel.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
            {
                Title = "Select Video File",
                AllowMultiple = false
            });

            if (files.Count > 0)
            {
                string videoPath = files[0].Path.LocalPath;
                using var media = new Media(_libVlc, videoPath, FromType.FromPath);
                _mediaPlayer?.Play(media);

                _intervalStartMs = 0;
                _isSecondPass = false;

                if (StatusText != null)
                    StatusText.Text = "Status: Playing video...";
            }
        }

        private async void OnOpenJsonClicked(object? sender, RoutedEventArgs e)
        {
            var topLevel = TopLevel.GetTopLevel(this);
            if (topLevel == null) return;

            var files = await topLevel.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
            {
                Title = "Select Subtitle JSON File",
                AllowMultiple = false
            });

            if (files.Count > 0)
            {
                LoadSubtitlesFromFile(files[0].Path.LocalPath);
            }
        }

        private void LoadSubtitlesFromFile(string jsonPath)
        {
            _subtitles.Clear();

            if (File.Exists(jsonPath))
            {
                try
                {
                    string jsonContent = File.ReadAllText(jsonPath);
                    var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                    var items = JsonSerializer.Deserialize<List<SubtitleItem>>(jsonContent, options);

                    if (items != null)
                    {
                        _subtitles = items;
                        if (StatusText != null)
                            StatusText.Text = $"Status: Loaded {_subtitles.Count} subtitles!";
                    }
                }
                catch (Exception ex)
                {
                    if (StatusText != null)
                        StatusText.Text = $"Status: JSON Error - {ex.Message}";
                }
            }
        }

        private void OnLoopTimerTick(object? sender, EventArgs e)
        {
            if (_mediaPlayer == null || !_mediaPlayer.IsPlaying) return;

            long currentTimeMs = _mediaPlayer.Time;
            double currentTimeSeconds = (double)currentTimeMs / 1000.0;
            long targetEnd = _intervalStartMs + IntervalMs;

            Dispatcher.UIThread.Post(() =>
            {
                // Display subtitles ONLY during Pass 2 AND if TextEs is not empty
                if (_isSecondPass)
                {
                    var currentSub = _subtitles.FirstOrDefault(s => currentTimeSeconds >= s.Start && currentTimeSeconds <= s.End);

                    if (currentSub != null && !string.IsNullOrWhiteSpace(currentSub.TextEs))
                    {
                        if (TextEnBlock != null) TextEnBlock.Text = currentSub.TextEn;
                        if (TextEsBlock != null) TextEsBlock.Text = currentSub.TextEs;
                    }
                    else
                    {
                        if (TextEnBlock != null) TextEnBlock.Text = string.Empty;
                        if (TextEsBlock != null) TextEsBlock.Text = string.Empty;
                    }
                }
                else
                {
                    // Pass 1: Keep subtitles completely hidden
                    if (TextEnBlock != null) TextEnBlock.Text = string.Empty;
                    if (TextEsBlock != null) TextEsBlock.Text = string.Empty;
                }
            });

            // Check end of 15-second window
            if (currentTimeMs >= targetEnd)
            {
                double intervalStartSec = (double)_intervalStartMs / 1000.0;
                double intervalEndSec = (double)targetEnd / 1000.0;

                // Check if any subtitle in the current 15s window has a valid TextEs
                bool hasSpanishSub = _subtitles.Any(s =>
                    s.Start < intervalEndSec &&
                    s.End > intervalStartSec &&
                    !string.IsNullOrWhiteSpace(s.TextEs));

                if (!_isSecondPass && hasSpanishSub)
                {
                    // Repeat segment for Pass 2 with subtitles
                    _mediaPlayer.Time = _intervalStartMs;
                    _isSecondPass = true;

                    if (StatusText != null)
                        StatusText.Text = "Status: Repeating segment (Pass 2 - With Subtitles)";
                }
                else
                {
                    // Skip Pass 2 if TextEs is empty, OR finish Pass 2 and advance to next interval
                    _intervalStartMs = targetEnd;
                    _isSecondPass = false;

                    if (StatusText != null)
                        StatusText.Text = "Status: Playing next segment (Pass 1 - No Subtitles)";
                }
            }
        }
    }
}