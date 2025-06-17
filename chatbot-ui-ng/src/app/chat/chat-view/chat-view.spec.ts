import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatView } from './chat-view';

describe('ChatView', () => {
  let component: ChatView;
  let fixture: ComponentFixture<ChatView>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatView]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatView);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
