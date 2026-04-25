import { cn } from "@/lib/utils";

export const Spinner = ({ className }: { className?: string }) => {
  return (
    <div
      className={cn(
        "h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent",
        className
      )}
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};
