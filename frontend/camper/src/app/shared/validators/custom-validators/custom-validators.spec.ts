import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomValidators } from './custom-validators';

describe('CustomValidators', () => {
  let component: CustomValidators;
  let fixture: ComponentFixture<CustomValidators>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomValidators]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomValidators);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
