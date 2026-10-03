using System.Text.Json.Serialization;

namespace CustomVideoPlayer.Models;

public class SubtitleItem
{
    [JsonPropertyName("start")]
    public double Start { get; set; }

    [JsonPropertyName("end")]
    public double End { get; set; }

    [JsonPropertyName("textEn")]
    public string TextEn { get; set; } = string.Empty;

    [JsonPropertyName("textEs")]
    public string TextEs { get; set; } = string.Empty;
}