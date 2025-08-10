import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  animation?: 'pulse' | 'wave' | 'none';
  width?: string | number;
  height?: string | number;
}

export default function Skeleton({
  className,
  variant = 'text',
  animation = 'pulse',
  width,
  height,
}: SkeletonProps) {
  const baseClasses = 'bg-gray-200 dark:bg-gray-700';
  
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };

  const style: React.CSSProperties = {
    width: width || (variant === 'circular' ? '40px' : '100%'),
    height: height || (variant === 'text' ? '20px' : variant === 'circular' ? '40px' : '100px'),
  };

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      style={style}
    />
  );
}

// Composite Skeleton Components
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('bg-white rounded-lg p-6 shadow-sm', className)}>
      <Skeleton variant="rectangular" height={200} className="mb-4" />
      <Skeleton variant="text" className="mb-2" />
      <Skeleton variant="text" width="60%" />
    </div>
  );
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center space-x-4">
          <Skeleton variant="circular" />
          <div className="flex-1">
            <Skeleton variant="text" className="mb-2" />
            <Skeleton variant="text" width="75%" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead>
          <tr>
            {Array.from({ length: columns }).map((_, index) => (
              <th key={index} className="px-6 py-3">
                <Skeleton variant="text" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex} className="px-6 py-4">
                  <Skeleton variant="text" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function SkeletonForm() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton variant="text" width={100} height={16} className="mb-2" />
        <Skeleton variant="rectangular" height={40} />
      </div>
      <div>
        <Skeleton variant="text" width={100} height={16} className="mb-2" />
        <Skeleton variant="rectangular" height={40} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Skeleton variant="text" width={80} height={16} className="mb-2" />
          <Skeleton variant="rectangular" height={40} />
        </div>
        <div>
          <Skeleton variant="text" width={80} height={16} className="mb-2" />
          <Skeleton variant="rectangular" height={40} />
        </div>
      </div>
      <Skeleton variant="rectangular" height={40} width={120} />
    </div>
  );
}
