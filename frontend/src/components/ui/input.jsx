import * as React from "react"

import { cn } from "../../lib/utils"

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        "flex h-12 w-full rounded-xl border-2 border-[#f4d03f]/30 bg-black/40 backdrop-blur-sm px-4 py-3 text-base text-[#f0f0f0] shadow-lg transition-all duration-300 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-[#f4d03f] placeholder:text-[#888888] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#f4d03f] focus-visible:ring-offset-2 focus-visible:ring-offset-black focus-visible:border-[#f4d03f] focus-visible:bg-black/60 focus-visible:shadow-xl focus-visible:shadow-[#f4d03f]/20 disabled:cursor-not-allowed disabled:opacity-50 hover:border-[#f4d03f]/50 hover:bg-black/50",
        className
      )}
      ref={ref}
      {...props} />
  );
})
Input.displayName = "Input"

export { Input }