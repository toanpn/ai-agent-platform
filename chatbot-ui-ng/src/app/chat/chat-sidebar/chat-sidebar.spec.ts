import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatSidebar } from './chat-sidebar';

describe('ChatSidebar', () => {
  let component: ChatSidebar;
  let fixture: ComponentFixture<ChatSidebar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatSidebar]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatSidebar);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
