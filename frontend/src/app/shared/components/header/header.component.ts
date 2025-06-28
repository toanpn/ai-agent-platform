import {
	Component,
	Input,
	Output,
	EventEmitter,
	ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';
import { User } from '../../../core/services/auth.service';
import { LanguagePickerComponent } from '../language-picker/language-picker.component';

@Component({
	selector: 'app-header',
	standalone: true,
	imports: [
		CommonModule,
		MatButtonModule,
		MatIconModule,
		MatMenuModule,
		TranslateModule,
		LanguagePickerComponent,
	],
	templateUrl: './header.component.html',
	styleUrls: ['./header.component.scss'],
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent {
	@Input() loggedUser!: User;
	@Output() logout = new EventEmitter<void>();

	onLogout(): void {
		this.logout.emit();
	}
} 