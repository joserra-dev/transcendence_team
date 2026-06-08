import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParkingDetail } from './parking-detail';

describe('ParkingDetail', () => {
  let component: ParkingDetail;
  let fixture: ComponentFixture<ParkingDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ParkingDetail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ParkingDetail);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
