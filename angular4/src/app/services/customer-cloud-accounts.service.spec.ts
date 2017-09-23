/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { CustomerCloudAccountsService } from './customer-cloud-accounts.service';

describe('CustomerCloudAccountsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [CustomerCloudAccountsService]
    });
  });

  it('should ...', inject([CustomerCloudAccountsService], (service: CustomerCloudAccountsService) => {
    expect(service).toBeTruthy();
  }));
});
