// Utility functions for the frontend

export function getSeverityColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'low':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'high':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

export function getUrgencyColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'normal':
      return 'bg-blue-100 text-blue-800';
    case 'high':
      return 'bg-orange-100 text-orange-800';
    case 'critical':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

export function formatTime(minutes: number): string {
  if (minutes < 60) {
    return `${Math.round(minutes)} minutes`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return `${hours}h ${mins}m`;
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getEventCauseLabel(cause: string): string {
  return cause.replace(/_/g, ' ').toUpperCase();
}

export function isHighSeverity(severity: string): boolean {
  return severity.toLowerCase() === 'high';
}

export function isCriticalUrgency(urgency: string): boolean {
  return urgency.toLowerCase() === 'critical';
}
