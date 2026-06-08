import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageParking } from './manage-parking';

describe('ManageParking', () => {
  let component: ManageParking;
  let fixture: ComponentFixture<ManageParking>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageParking]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ManageParking);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
