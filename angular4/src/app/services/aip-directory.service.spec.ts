/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { AipDirectoryService } from './aip-directory.service';

describe('AipDirectoryService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AipDirectoryService]
    });
  });

  it('should ...', inject([AipDirectoryService], (service: AipDirectoryService) => {
    expect(service).toBeTruthy();
  }));
});
