import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatInput } from './chat-input';

describe('ChatInput', () => {
  let component: ChatInput;
  let fixture: ComponentFixture<ChatInput>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatInput]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatInput);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
