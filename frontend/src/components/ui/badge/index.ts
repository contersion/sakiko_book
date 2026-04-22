import { cva, type VariantProps } from "class-variance-authority";

export { default as Badge } from "./Badge.vue";

export const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-[var(--badge-default-bg)] text-[var(--badge-default-text)] hover:bg-[var(--badge-default-hover)]",
        secondary: "border-transparent bg-[var(--badge-secondary-bg)] text-[var(--badge-secondary-text)] hover:bg-[var(--badge-secondary-hover)]",
        destructive: "border-transparent bg-[var(--badge-destructive-bg)] text-[var(--badge-destructive-text)] hover:bg-[var(--badge-destructive-hover)]",
        outline: "text-[var(--badge-outline-text)] border-[var(--badge-outline-border)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export type BadgeVariants = VariantProps<typeof badgeVariants>;
