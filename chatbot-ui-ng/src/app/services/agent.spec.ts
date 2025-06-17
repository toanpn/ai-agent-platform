import { TestBed } from '@angular/core/testing';

import { Agent } from './agent';

describe('Agent', () => {
  let service: Agent;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Agent);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
