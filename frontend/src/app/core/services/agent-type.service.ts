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
		marketing: { type: 'marketing', avatar: 'assets/icons/agent-marketing-avatar.png', color: 'teal' },
		hr: { type: 'hr', avatar: 'assets/icons/agent-marketing-avatar.png', color: 'teal' },
		'l&d': { type: 'ld', avatar: 'assets/icons/agent-marketing-avatar.png', color: 'cyan' },
		ic: { type: 'ic', avatar: 'assets/icons/agent-marketing-avatar.png', color: 'emerald' },
		employee: { type: 'employee', avatar: 'assets/icons/agent-marketing-avatar.png', color: 'sky' },

		// Finance & Business
		finance: { type: 'finance', avatar: 'assets/icons/agent-finance-avatar.png', color: 'sky' },
		financial: { type: 'finance', avatar: 'assets/icons/agent-finance-avatar.png', color: 'sky' },
		om: { type: 'om', avatar: 'assets/icons/agent-finance-avatar.png', color: 'emerald' },
		cnb: { type: 'cnb', avatar: 'assets/icons/agent-finance-avatar.png', color: 'lime' },
		booking: { type: 'booking', avatar: 'assets/icons/agent-finance-avatar.png', color: 'sky' },
		retail: { type: 'retail', avatar: 'assets/icons/agent-finance-avatar.png', color: 'cyan' },
		fnb: { type: 'fnb', avatar: 'assets/icons/agent-finance-avatar.png', color: 'cyan' },

		// Data & Technology
		data: { type: 'data', avatar: 'assets/icons/agent-data-avatar.png', color: 'emerald' },
		it: { type: 'it', avatar: 'assets/icons/agent-data-avatar.png', color: 'sky' },
		'ai research': { type: 'ai-research', avatar: 'assets/icons/agent-data-avatar.png', color: 'teal' },
		kms: { type: 'kms', avatar: 'assets/icons/agent-data-avatar.png', color: 'cyan' },

		// Default
		general: { type: 'default', avatar: 'assets/icons/user-avatar.png', color: 'cyan' },
		default: { type: 'default', avatar: 'assets/icons/user-avatar.png', color: 'cyan' },
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
