"use client";

interface PriorityGaugeProps {
  value: number;
  size?: number;
}

function getPriorityConfig(value: number) {
  if (value >= 81) return { label: "TOP", color: "#10b981", tailwind: "emerald" };
  if (value >= 61) return { label: "HIGH", color: "#eab308", tailwind: "yellow" };
  if (value >= 41) return { label: "MED", color: "#f97316", tailwind: "orange" };
  return { label: "LOW", color: "#ef4444", tailwind: "red" };
}

export function PriorityGauge({ value, size = 160 }: PriorityGaugeProps) {
  const config = getPriorityConfig(value);
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * Math.PI * 1.5; // 270 degrees (3/4 circle)
  const progress = (value / 100) * circumference;
  const center = size / 2;

  return (
    <div className="relative flex items-center justify-center">
      <svg
        width={size}
        height={size}
        className="transform rotate-[135deg]"
      >
        {/* Define gradient and glow filter */}
        <defs>
          <linearGradient id="priorityGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="33%" stopColor="#f97316" />
            <stop offset="66%" stopColor="#eab308" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          <filter id="innerShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="blur"/>
            <feOffset dx="0" dy="2"/>
            <feComposite in2="SourceAlpha" operator="arithmetic" k2="-1" k3="1"/>
            <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.3 0"/>
            <feBlend in2="SourceGraphic"/>
          </filter>
        </defs>

        {/* Background track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth={strokeWidth}
          strokeDasharray={`${circumference} ${circumference * 0.333}`}
          strokeLinecap="round"
        />

        {/* Progress arc with glow */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={config.color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${progress} ${circumference}`}
          strokeLinecap="round"
          filter="url(#glow)"
          className="transition-all duration-700 ease-out"
          style={{
            filter: `drop-shadow(0 0 12px ${config.color})`
          }}
        />

        {/* Subtle tick marks */}
        {[0, 25, 50, 75, 100].map((tick) => {
          const angle = (tick / 100) * 270 - 135;
          const rad = (angle * Math.PI) / 180;
          const innerR = radius - strokeWidth / 2 - 8;
          const outerR = radius - strokeWidth / 2 - 4;
          return (
            <line
              key={tick}
              x1={center + innerR * Math.cos(rad)}
              y1={center + innerR * Math.sin(rad)}
              x2={center + outerR * Math.cos(rad)}
              y2={center + outerR * Math.sin(rad)}
              stroke="rgba(255,255,255,0.2)"
              strokeWidth="2"
              strokeLinecap="round"
            />
          );
        })}
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="text-5xl font-bold tracking-tight transition-all duration-500"
          style={{
            color: config.color,
            textShadow: `0 0 30px ${config.color}40, 0 0 60px ${config.color}20`
          }}
        >
          {value}
        </span>
        <span
          className="text-sm font-bold uppercase tracking-[0.2em] mt-1 transition-all duration-500"
          style={{ color: config.color }}
        >
          {config.label}
        </span>
      </div>
    </div>
  );
}
