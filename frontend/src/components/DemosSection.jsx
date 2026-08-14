import React from "react";
import { PlayCircle } from "lucide-react";
import { projects, featuredShowcaseVideo } from "../mock";
import { toYouTubeEmbed, isVideoFile } from "../utils/youtube";

const Placeholder = () => (
  <div className="absolute inset-0 flex flex-col items-center justify-center">
    <div className="grid-bg absolute inset-0 opacity-30" />
    <span className="relative grid h-12 w-12 place-items-center rounded-full border border-red-600/50 bg-red-600/10">
      <PlayCircle className="h-6 w-6 text-red-500" />
    </span>
    <p className="relative mt-3 font-tech text-sm text-zinc-400">Demo video coming soon</p>
    <p className="relative font-mono2 text-[11px] text-zinc-600">/ slot reserved</p>
  </div>
);

const VideoFrame = ({ url, title }) => {
  const embed = toYouTubeEmbed(url);
  if (embed) {
    return (
      <iframe
        className="absolute inset-0 h-full w-full"
        src={embed}
        title={title}
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      />
    );
  }
  if (isVideoFile(url)) {
    return <video className="absolute inset-0 h-full w-full object-cover" src={url} controls playsInline preload="metadata" />;
  }
  return <Placeholder />;
};

const DemoSlot = ({ project }) => (
  <div className="tech-card group flex flex-col overflow-hidden clip-corner">
    <div className="flex items-center gap-3 border-b border-zinc-800/80 p-4">
      <img src={project.image} alt={project.name} className="h-10 w-10 rounded-md border border-zinc-700 object-contain bg-black p-0.5" />
      <div>
        <p className="font-display text-sm font-bold text-white">{project.name}</p>
        <p className="font-mono2 text-[11px] text-red-400">Gameplay demo</p>
      </div>
    </div>
    <div className="relative aspect-video w-full bg-black">
      <VideoFrame url={project.demoVideo} title={`${project.name} demo`} />
    </div>
  </div>
);

const DemosSection = () => {
  return (
    <section id="demos" className="relative border-t border-zinc-800/80 py-20 md:py-28">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Gameplay / demos</p>
          <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-5xl">
            See each build <span className="text-red-500">in action</span>
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-sm text-zinc-500">
            A short gameplay demonstration for every project, straight from live lobbies.
          </p>
        </div>

        {/* Featured showcase reel */}
        <div className="mx-auto mt-12 max-w-4xl">
          <div className="tech-card overflow-hidden clip-corner">
            <div className="flex items-center justify-between border-b border-zinc-800/80 p-4">
              <p className="font-display text-sm font-bold text-white">Featured gameplay reel</p>
              <span className="font-mono2 text-[11px] uppercase tracking-widest text-red-400">Live footage</span>
            </div>
            <div className="relative aspect-video w-full bg-black">
              <VideoFrame url={featuredShowcaseVideo} title="Featured gameplay reel" />
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          {projects.map((p) => (
            <DemoSlot key={p.id} project={p} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default DemosSection;
