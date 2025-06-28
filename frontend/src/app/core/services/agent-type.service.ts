import { Injectable } from '@angular/core';

export interface DepartmentConfig {
	type: string;
	avatar: string;
	// Base color for UI elements like tags and headers
	color: string;
}

@Injectable({
	providedIn: 'root',
})
export class AgentTypeService {
	// A map from a searchable keyword to its full configuration
	private readonly departmentConfigs: Record<string, DepartmentConfig> = {
		// Marketing & HR
		marketing: { type: 'marketing', avatar: 'assets/icons/agent-marketing-avatar.svg', color: 'purple' },
		hr: { type: 'hr', avatar: 'assets/icons/agent-hr-avatar.svg', color: 'red' },
		'l&d': { type: 'ld', avatar: 'assets/icons/agent-ld-avatar.svg', color: 'lime' },
		ic: { type: 'ic', avatar: 'assets/icons/agent-ic-avatar.svg', color: 'emerald' },
		employee: { type: 'employee', avatar: 'assets/icons/agent-employee-avatar.svg', color: 'purple' },

		// Finance & Business
		finance: { type: 'finance', avatar: 'assets/icons/agent-finance-avatar.svg', color: 'blue' },
		financial: { type: 'finance', avatar: 'assets/icons/agent-finance-avatar.svg', color: 'blue' },
		om: { type: 'om', avatar: 'assets/icons/agent-om-avatar.svg', color: 'orange' },
		cnb: { type: 'cnb', avatar: 'assets/icons/agent-cnb-avatar.svg', color: 'yellow' },
		booking: { type: 'booking', avatar: 'assets/icons/agent-booking-avatar.svg', color: 'pink' },
		retail: { type: 'retail', avatar: 'assets/icons/agent-retail-avatar.svg', color: 'indigo' },
		fnb: { type: 'fnb', avatar: 'assets/icons/agent-fnb-avatar.svg', color: 'cyan' },

		// Data & Technology
		data: { type: 'data', avatar: 'assets/icons/agent-data-avatar.svg', color: 'green' },
		it: { type: 'it', avatar: 'assets/icons/agent-it-avatar.svg', color: 'sky' },
		'ai research': { type: 'ai-research', avatar: 'assets/icons/agent-ai-research-avatar.svg', color: 'teal' },
		kms: { type: 'kms', avatar: 'assets/icons/agent-kms-avatar.svg', color: 'gray' },

		// Default
		general: { type: 'default', avatar: 'assets/icons/agent.svg', color: 'gray' },
		default: { type: 'default', avatar: 'assets/icons/agent.svg', color: 'gray' },
	};

	private findConfig(departmentName: string): DepartmentConfig {
		const department = departmentName.toLowerCase();
		for (const key of Object.keys(this.departmentConfigs)) {
			if (department.includes(key)) {
				return this.departmentConfigs[key];
			}
		}
		return this.departmentConfigs['default'];
	}

	getAgentType(agent?: { department?: string }): string {
		if (!agent?.department) {
			return 'default';
		}
		return this.findConfig(agent.department).type;
	}

	getAgentAvatar(agent?: { department?: string }): string {
		if (!agent?.department) {
			return this.departmentConfigs['default'].avatar;
		}
		return this.findConfig(agent.department).avatar;
	}
} 
