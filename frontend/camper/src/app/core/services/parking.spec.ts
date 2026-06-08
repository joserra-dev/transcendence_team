import { TestBed } from '@angular/core/testing';

import { ParkingService } from './parking';

describe('Parking', () => {
  let service: ParkingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ParkingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
