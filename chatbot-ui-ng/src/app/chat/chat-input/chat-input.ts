import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormsModule, ReactiveFormsModule } from '@angular/forms';

@Component({
	selector: 'app-chat-input',
	imports: [FormsModule, ReactiveFormsModule],
	templateUrl: './chat-input.html',
	styleUrl: './chat-input.css',
})
export class ChatInput {
	@Output() sendMessage = new EventEmitter<string>();
	messageForm: FormGroup;

	constructor(private fb: FormBuilder) {
		this.messageForm = this.fb.group({
			message: ['', [Validators.required]],
		});
	}

	onSubmit() {
		if (this.messageForm.valid) {
			this.sendMessage.emit(this.messageForm.value.message);
			this.messageForm.reset();
		}
	}
}
