/**
 * The page's signature element. Plowed-field furrow ridges rendered as a
 * repeating SVG pattern — used as section dividers throughout the site
 * instead of a generic straight <hr>. A real visual callback to the
 * subject (a field, tilled in rows) rather than decoration for its own sake.
 */
export default function FurrowDivider({ color = "#E8A93D", className = "" }) {
  return (
    <div className={`w-full overflow-hidden leading-none ${className}`} aria-hidden="true">
      <svg
        viewBox="0 0 1200 32"
        preserveAspectRatio="none"
        className="w-full h-4"
      >
        {Array.from({ length: 12 }).map((_, i) => (
          <path
            key={i}
            d={`M ${i * 100} 32 Q ${i * 100 + 50} 0 ${i * 100 + 100} 32`}
            fill="none"
            stroke={color}
            strokeWidth="1.5"
            opacity={0.35 + (i % 3) * 0.12}
          />
        ))}
      </svg>
    </div>
  );
}
