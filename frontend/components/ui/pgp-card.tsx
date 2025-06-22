import React from 'react';

const PGPCard = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={`rounded-[var(--radius)] bg-card border border-card-border text-card-foreground shadow-lg ${className}`}
    {...props}
  />
));
PGPCard.displayName = 'PGPCard';

const PGPCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={`flex flex-col space-y-1.5 p-6 ${className}`}
    {...props}
  />
));
PGPCardHeader.displayName = 'PGPCardHeader';

const PGPCardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={`text-lg font-semibold leading-none tracking-tight text-foreground ${className}`}
    {...props}
  />
));
PGPCardTitle.displayName = 'PGPCardTitle';

const PGPCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={`p-6 pt-0 ${className}`} {...props} />
));
PGPCardContent.displayName = 'PGPCardContent';

export { PGPCard, PGPCardHeader, PGPCardTitle, PGPCardContent };