import type { ButtonHTMLAttributes } from 'react'

type ButtonVariant = 'primary' | 'ghost' | 'outline'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  loading?: boolean
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-[var(--button-primary-bg)] text-[var(--color-primary-foreground)] hover:bg-[var(--button-primary-hover)] border border-[var(--color-border-subtle)]',
  ghost:
    'bg-transparent text-[var(--color-muted-foreground)] hover:bg-[var(--button-ghost-hover)] hover:text-[var(--color-foreground)]',
  outline:
    'bg-transparent text-[var(--color-foreground)] border border-[var(--color-border-subtle)] hover:border-[var(--color-cream-300)]',
}

export function Button({
  variant = 'primary',
  loading = false,
  className = '',
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] px-5 py-2.5 text-sm font-medium transition-colors duration-200 disabled:cursor-not-allowed disabled:opacity-50 ${variantClasses[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          {children}
        </>
      ) : (
        children
      )}
    </button>
  )
}
