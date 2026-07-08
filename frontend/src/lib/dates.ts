export function parseLocalDate(value: string): Date {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

export function formatLocalDate(
  value: string,
  options: Intl.DateTimeFormatOptions,
  locale = 'es-AR',
): string {
  return new Intl.DateTimeFormat(locale, options).format(parseLocalDate(value))
}

export function daysBetween(startDate: string, endDate: string): number {
  const start = parseLocalDate(startDate)
  const end = parseLocalDate(endDate)
  return Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
}
