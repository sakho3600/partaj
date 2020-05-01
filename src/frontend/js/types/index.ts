export enum UnitMembershipRole {
  ADMIN = 'admin',
  MEMBER = 'member',
  OWNER = 'owner',
}

export enum ReferralState {
  ASSIGNED = 'assigned',
  RECEIVED = 'received',
  CLOSED = 'closed',
  INCOMPLETE = 'incomplete',
  ANSWERED = 'answered',
}

export interface User {
  date_joined: string;
  email: string;
  first_name: string;
  id: string;
  is_staff: boolean;
  is_superuser: boolean;
  last_name: string;
  unite: string;
  username: string;
}

export interface UnitMember extends User {
  membership: UnitMembership;
}

export interface UnitMembership {
  created_at: string;
  id: string;
  role: UnitMembershipRole;
  updated_at: string;
  user: string;
  unit: string;
}

export interface Unit {
  created_at: string;
  id: string;
  members: UnitMember[];
  name: string;
}

export interface Topic {
  created_at: string;
  id: string;
  name: string;
  unit: Unit;
}

export interface Referral {
  assignees: User['id'][];
  context: string;
  created_at: string;
  id: number;
  prior_work: string;
  question: string;
  requester: string;
  state: ReferralState;
  topic: Topic;
  updated_at: string;
  urgency: string;
  urgency_explanation: string;
  user: User;
}
