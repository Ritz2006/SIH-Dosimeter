// Placeholder worker records. In production this comes from the
// Go/Gin backend's /workers endpoint — see backend-dummy/data for
// the equivalent seed JSON your teammate can load into SQLite.

export const workers = [
  {
    id: 'W-001',
    name: 'Rahul Kumar',
    role: 'Field Technician',
    site: 'Field Site B-12',
    badgeId: 'H2S-00127'
  },
  {
    id: 'W-002',
    name: 'Amit Sharma',
    role: 'Pipeline Inspector',
    site: 'Field Site B-12',
    badgeId: 'H2S-00128'
  },
  {
    id: 'W-003',
    name: 'Priya Singh',
    role: 'Safety Officer',
    site: 'Field Site B-07',
    badgeId: 'H2S-00129'
  },
  {
    id: 'W-004',
    name: 'Mohan Das',
    role: 'Field Technician',
    site: 'Field Site B-07',
    badgeId: 'H2S-00131'
  }
]
