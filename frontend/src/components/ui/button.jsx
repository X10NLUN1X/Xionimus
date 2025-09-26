import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority";

import { cn } from "../../lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#f4d03f] focus-visible:ring-offset-2 focus-visible:ring-offset-black disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 transform hover:scale-105 active:scale-95",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-br from-[#f4d03f] via-[#d4af37] to-[#b8860b] text-black shadow-lg shadow-[#f4d03f]/30 hover:shadow-xl hover:shadow-[#f4d03f]/40 border border-[#f4d03f]/20",
        destructive:
          "bg-gradient-to-br from-red-600 to-red-700 text-white shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40",
        outline:
          "border-2 border-[#f4d03f] bg-transparent text-[#f4d03f] shadow-sm hover:bg-[#f4d03f]/10 hover:text-[#f9e79f] backdrop-blur-sm",
        secondary:
          "bg-gradient-to-br from-zinc-800 to-zinc-900 text-white border border-[#f4d03f]/30 shadow-lg hover:border-[#f4d03f]/50 hover:shadow-[#f4d03f]/20",
        ghost: 
          "bg-transparent text-[#f0f0f0] hover:bg-[#f4d03f]/15 hover:text-[#f4d03f] backdrop-blur-sm",
        link: 
          "text-[#f4d03f] underline-offset-4 hover:underline hover:text-[#f9e79f] bg-transparent",
        premium:
          "bg-gradient-to-br from-black via-zinc-900 to-[#f4d03f]/20 text-[#f4d03f] border-2 border-[#f4d03f] shadow-lg shadow-[#f4d03f]/25 hover:shadow-2xl hover:shadow-[#f4d03f]/40 backdrop-blur-sm",
      },
      size: {
        default: "h-11 px-6 py-3",
        sm: "h-9 rounded-lg px-4 text-xs",
        lg: "h-13 rounded-xl px-10 text-base",
        icon: "h-11 w-11",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button"
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props} />
  );
})
Button.displayName = "Button"

export { Button, buttonVariants }