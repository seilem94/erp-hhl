import type { SVGProps } from 'react'

type IconName = 'arrow-right' | 'blueprint' | 'chart' | 'check' | 'chevron-down' | 'close' | 'menu' | 'plus' | 'receipt' | 'settings' | 'user'

type IconProps = SVGProps<SVGSVGElement> & { name: IconName }

const paths: Record<IconName, string[]> = {
  'arrow-right': ['M5 12h14', 'm13 6 6 6-6 6'],
  blueprint: ['M4 5h16v16H4z', 'M4 10h16', 'M10 10v11', 'M14 14h3v3', 'M7 3v4', 'M13 3v4', 'M17 3v4'],
  chart: ['M4 4v16h16', 'M8 15v-4', 'M13 15V7', 'M18 15v-6'],
  check: ['m5 12 4 4L19 6'],
  'chevron-down': ['m6 9 6 6 6-6'],
  close: ['m6 6 12 12', 'M6 18 18 6'],
  menu: ['M4 6h16', 'M4 12h16', 'M4 18h16'],
  plus: ['M12 5v14', 'M5 12h14'],
  receipt: ['M6 3h12v18l-3-2-3 2-3-2-3 2V3Z', 'M9 7h6', 'M9 11h6', 'M9 15h3'],
  settings: ['M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1 1-3Z', 'M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z'],
  user: ['M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z', 'M4 21v-2a8 8 0 0 1 16 0v2'],
}

export function Icon({ name, ...props }: IconProps) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>
      {paths[name].map((path) => <path key={path} d={path} />)}
    </svg>
  )
}
