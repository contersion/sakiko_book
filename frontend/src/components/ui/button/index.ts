import { cva, type VariantProps } from "class-variance-authority";

export { default as Button } from "./Button.vue";

export const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-400 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-[var(--button-default-bg)] text-[var(--button-default-text)] hover:bg-[var(--button-default-hover)]",
        destructive: "bg-[var(--button-destructive-bg)] text-white hover:bg-[var(--button-destructive-hover)]",
        outline: "border border-[var(--button-outline-border)] bg-[var(--button-outline-bg)] text-[var(--button-outline-text)] hover:bg-[var(--button-outline-hover)]",
        secondary: "bg-[var(--button-secondary-bg)] text-[var(--button-secondary-text)] hover:bg-[var(--button-secondary-hover)] border border-[var(--button-secondary-border)]",
        ghost: "text-[var(--button-ghost-text)] hover:bg-[var(--button-ghost-hover)] hover:text-[var(--text-primary)]",
        link: "text-[var(--button-link-text)] bg-[var(--button-link-bg)] hover:bg-[var(--button-link-hover-bg)] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export type ButtonVariants = VariantProps<typeof buttonVariants>;
