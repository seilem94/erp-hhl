import { request } from '@/api/client'
import { decodeProject, decodeProjects } from '@/api/decoders'
import type { CreateProjectRequest, ProjectResponse, UpdateProjectRequest } from '@/api/types'

export function getProjects(signal?: AbortSignal): Promise<ProjectResponse[]> {
  return request('/api/v1/projects/', decodeProjects, { signal })
}

export function createProject(body: CreateProjectRequest): Promise<ProjectResponse> {
  return request('/api/v1/projects/', decodeProject, { method: 'POST', body })
}

export function updateProject(projectId: string, body: UpdateProjectRequest): Promise<ProjectResponse> {
  return request(`/api/v1/projects/${encodeURIComponent(projectId)}`, decodeProject, { method: 'PATCH', body })
}
