// Placeholder badge records. `status` is normally derived from
// activatedOn + shelfLifeDays by the backend; kept pre-computed
// here since this folder is dummy data only.

export const badges = [
  {
    badgeId: 'H2S-00127',
    workerId: 'W-001',
    activatedOn: '2026-09-01',
    shelfLifeDays: 30,
    expiresOn: '2026-09-30',
    status: 'valid'
  },
  {
    badgeId: 'H2S-00128',
    workerId: 'W-002',
    activatedOn: '2026-08-20',
    shelfLifeDays: 30,
    expiresOn: '2026-09-19',
    status: 'valid'
  },
  {
    badgeId: 'H2S-00129',
    workerId: 'W-003',
    activatedOn: '2026-07-15',
    shelfLifeDays: 30,
    expiresOn: '2026-08-14',
    status: 'expired'
  },
  {
    badgeId: 'H2S-00131',
    workerId: 'W-004',
    activatedOn: '2026-09-03',
    shelfLifeDays: 30,
    expiresOn: '2026-10-03',
    status: 'valid'
  }
]
