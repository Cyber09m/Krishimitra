import { useEffect, useState } from "react";

/**
 * The genuinely-real-time part of the "real-time weather" feature: a
 * per-second ticking countdown to the next data refresh, plus a live
 * "last updated Xs ago" readout. The underlying weather data refetches
 * every `intervalSeconds` (data doesn't change meaningfully faster than
 * that), but this indicator itself updates every second so the UI always
 * feels alive rather than static between refreshes.
 */
export default function LiveIndicator({ intervalSeconds, lastUpdatedAt, onTick }) {
  const [secondsAgo, setSecondsAgo] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      if (!lastUpdatedAt) return;
      const elapsed = Math.floor((Date.now() - lastUpdatedAt) / 1000);
      setSecondsAgo(elapsed);
      if (elapsed > 0 && elapsed % intervalSeconds === 0 && onTick) {
        onTick();
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [lastUpdatedAt, intervalSeconds, onTick]);

  const secondsUntilNext = Math.max(intervalSeconds - (secondsAgo % intervalSeconds), 0);

  return (
    <div className="flex items-center gap-2 text-xs font-mono text-wheat-dim">
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-400" />
      </span>
      <span>Live · updated {secondsAgo}s ago · next in {secondsUntilNext}s</span>
    </div>
  );
}
