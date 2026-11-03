import { request } from '@/api/client'
import { decodeProject, decodeProjects } from '@/api/decoders'
import type { CreateProjectRequest, ProjectResponse } from '@/api/types'

export function getProjects(signal?: AbortSignal): Promise<ProjectResponse[]> {
  return request('/api/v1/projects/', decodeProjects, { signal })
}

export function createProject(body: CreateProjectRequest): Promise<ProjectResponse> {
  return request('/api/v1/projects/', decodeProject, { method: 'POST', body })
}
