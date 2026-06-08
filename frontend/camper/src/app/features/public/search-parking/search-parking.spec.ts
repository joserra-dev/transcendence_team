import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchParking } from './search-parking';

describe('SearchParking', () => {
  let component: SearchParking;
  let fixture: ComponentFixture<SearchParking>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchParking]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SearchParking);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
