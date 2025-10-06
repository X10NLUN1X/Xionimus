import React, { forwardRef } from 'react'

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string
  label?: string
  helperText?: string
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ error, label, helperText, className = '', ...props }, ref) => {
    const id = props.id || `textarea-${Math.random().toString(36).substr(2, 9)}`

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={id}
            className="block text-sm font-medium text-gray-300 mb-2"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={id}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? `${id}-error` : helperText ? `${id}-helper` : undefined}
          className={`
            w-full px-4 py-3
            bg-primary-navy/50 backdrop-blur-md 
            border-2 rounded-xl
            text-white placeholder-gray-400
            focus:outline-none focus:ring-2 focus:ring-gold-500 focus:ring-offset-2 focus:ring-offset-primary-dark
            transition-all duration-300
            resize-none
            ${error 
              ? 'border-red-500 focus:border-red-500' 
              : 'border-gold-500/20 hover:border-gold-500/30 focus:border-gold-500'
            }
            ${className}
          `}
          {...props}
        />
        {error && (
          <p
            id={`${id}-error`}
            className="mt-2 text-sm text-red-400"
            role="alert"
          >
            {error}
          </p>
        )}
        {helperText && !error && (
          <p
            id={`${id}-helper`}
            className="mt-2 text-sm text-gray-400"
          >
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
