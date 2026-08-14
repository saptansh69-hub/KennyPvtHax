// YouTube URL helpers
export const toYouTubeId = (url) => {
  if (!url) return null;
  const m = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{11})/);
  return m ? m[1] : null;
};

// Standard embed (with light controls) for demo players
export const toYouTubeEmbed = (url) => {
  const id = toYouTubeId(url);
  return id ? `https://www.youtube.com/embed/${id}?rel=0&modestbranding=1&playsinline=1` : null;
};

// Muted, looping, controls-off embed for use as a blurred background
export const toYouTubeBg = (url) => {
  const id = toYouTubeId(url);
  if (!id) return null;
  const params = new URLSearchParams({
    autoplay: "1",
    mute: "1",
    controls: "0",
    loop: "1",
    playlist: id,
    playsinline: "1",
    modestbranding: "1",
    rel: "0",
    showinfo: "0",
    iv_load_policy: "3",
    disablekb: "1",
  });
  return `https://www.youtube.com/embed/${id}?${params.toString()}`;
};

export const isVideoFile = (url) => !!url && /\.(mp4|webm|mov)(\?.*)?$/i.test(url);
