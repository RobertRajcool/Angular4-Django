/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { RegisteredCustomersService } from './registered-customers.service';

describe('RegisteredCustomersService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [RegisteredCustomersService]
    });
  });

  it('should ...', inject([RegisteredCustomersService], (service: RegisteredCustomersService) => {
    expect(service).toBeTruthy();
  }));
});
