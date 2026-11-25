import { request } from '@/api/client'
import { decodeAuditLogPage } from '@/api/decoders'
import type { AuditFilters, AuditLogPage } from '@/api/types'

export function getAuditLogs(filters: AuditFilters, limit: number, offset: number, signal?: AbortSignal): Promise<AuditLogPage> {
  return request('/api/v1/audit-logs', decodeAuditLogPage, {
    signal,
    queryParams: { ...filters, limit: String(limit), offset: String(offset) },
  })
}
