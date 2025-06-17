import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AgentDetail } from './agent-detail';

describe('AgentDetail', () => {
  let component: AgentDetail;
  let fixture: ComponentFixture<AgentDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgentDetail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AgentDetail);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
