import type { ReactNode } from "react";
import { Link } from "zudoku/components";

/* ------------------------------------------------------------------ */
/* Value-add cards shown at the top of each use-case page              */
/* ------------------------------------------------------------------ */

export const ValueCards = ({ children }: { children: ReactNode }) => (
  <div className="not-prose my-8 grid grid-cols-1 gap-4 md:grid-cols-3">
    {children}
  </div>
);

export const ValueCard = ({
  title,
  metric,
  metricHref,
  children,
}: {
  title: string;
  metric?: string;
  metricHref?: string;
  children: ReactNode;
}) => (
  <div className="flex flex-col gap-2 rounded-lg border border-border border-t-2 border-t-primary bg-card p-5">
    <div className="font-semibold text-card-foreground">{title}</div>
    <div className="text-sm leading-relaxed text-muted-foreground [&_a]:text-primary [&_a]:underline-offset-2 [&_a:hover]:underline [&_p]:m-0">
      {children}
    </div>
    {metric &&
      (metricHref ? (
        <Link
          to={metricHref}
          className="mt-auto pt-3 font-mono text-sm text-primary underline-offset-2 hover:underline"
        >
          {metric}
        </Link>
      ) : (
        <div className="mt-auto pt-3 font-mono text-sm text-primary">
          {metric}
        </div>
      ))}
  </div>
);

/* ------------------------------------------------------------------ */
/* Simple left-to-right flow diagram                                   */
/* ------------------------------------------------------------------ */

export const UseCaseDiagram = ({
  caption,
  children,
}: {
  caption?: string;
  children: ReactNode;
}) => (
  <div className="not-prose my-8 rounded-lg border border-border bg-card p-6">
    <div className="flex flex-col items-stretch gap-4 lg:flex-row lg:items-center">
      {children}
    </div>
    {caption && (
      <div className="mt-6 border-t border-border pt-3 text-sm text-muted-foreground">
        {caption}
      </div>
    )}
  </div>
);

export const DiagramBox = ({
  title,
  note,
  accent,
  children,
}: {
  title: string;
  note?: string;
  accent?: boolean;
  children?: ReactNode;
}) => (
  <div
    className={`flex flex-1 flex-col gap-1.5 rounded-lg border p-4 ${
      accent
        ? "border-primary bg-primary/5"
        : "border-border bg-muted/40"
    }`}
  >
    <div
      className={`text-sm font-semibold ${
        accent ? "text-primary" : "text-card-foreground"
      }`}
    >
      {title}
    </div>
    {children && (
      <div className="text-sm leading-snug text-muted-foreground">
        {children}
      </div>
    )}
    {note && <div className="pt-1 font-mono text-xs text-primary">{note}</div>}
  </div>
);

export const DiagramArrow = ({
  label,
  sublabel,
  accent,
}: {
  label?: string;
  sublabel?: string;
  accent?: boolean;
}) => (
  <div className="flex shrink-0 flex-col items-center gap-1 px-2 py-1">
    {label && (
      <div
        className={`font-mono text-xs ${
          accent ? "text-primary" : "text-muted-foreground"
        }`}
      >
        {label}
      </div>
    )}
    <svg
      className={`h-3 w-16 rotate-90 lg:rotate-0 ${
        accent ? "text-primary" : "text-muted-foreground"
      }`}
      viewBox="0 0 64 12"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M0 6h58m0 0-6-5m6 5-6 5"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
    {sublabel && (
      <div className="font-mono text-xs text-muted-foreground">{sublabel}</div>
    )}
  </div>
);

export const DiagramStack = ({
  more,
  children,
}: {
  more?: string;
  children: ReactNode;
}) => (
  <div className="flex flex-1 flex-col gap-2">
    {children}
    {more && (
      <div className="rounded-lg border border-dashed border-border px-4 py-2.5 text-center text-xs text-muted-foreground">
        {more}
      </div>
    )}
  </div>
);

export const DiagramStackItem = ({
  label,
  chip,
}: {
  label: string;
  chip?: string;
}) => (
  <div className="flex items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-2.5">
    <div className="text-sm font-semibold text-card-foreground">{label}</div>
    {chip && (
      <div className="rounded bg-muted px-2 py-1 font-mono text-xs text-muted-foreground">
        {chip}
      </div>
    )}
  </div>
);

/* ------------------------------------------------------------------ */
/* Use-case index page                                                 */
/* ------------------------------------------------------------------ */

export const UseCaseGroup = ({
  title,
  note,
  children,
}: {
  title: string;
  note?: string;
  children: ReactNode;
}) => (
  <section className="not-prose my-10">
    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
      <h2 className="text-base font-bold text-foreground">{title}</h2>
      {note && <span className="text-sm text-muted-foreground">{note}</span>}
    </div>
    <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">{children}</div>
  </section>
);

export const UseCaseCard = ({
  title,
  href,
  tags,
  children,
}: {
  title: string;
  href: string;
  tags?: { label: string; href: string }[];
  children: ReactNode;
}) => (
  <div className="flex flex-col gap-2 rounded-lg border border-border bg-card p-5 transition-colors hover:border-primary/50">
    <h3 className="m-0 text-base font-semibold">
      <Link
        to={href}
        className="text-card-foreground underline-offset-2 hover:text-primary"
      >
        {title}
      </Link>
    </h3>
    <div className="text-sm leading-relaxed text-muted-foreground [&_p]:m-0">
      {children}
    </div>
    {tags && tags.length > 0 && (
      <div className="mt-auto flex flex-wrap items-center gap-x-2 gap-y-1 pt-2 font-mono text-xs">
        {tags.map((tag, i) => (
          <span key={`${tag.href}-${tag.label}`} className="flex items-center gap-2">
            {i > 0 && <span className="text-muted-foreground">·</span>}
            <Link
              to={tag.href}
              className="text-primary underline-offset-2 hover:underline"
            >
              {tag.label}
            </Link>
          </span>
        ))}
      </div>
    )}
  </div>
);
