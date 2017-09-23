/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { NotificationGroupsService } from './notification-groups.service';

describe('NotificationGroupsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [NotificationGroupsService]
    });
  });

  it('should ...', inject([NotificationGroupsService], (service: NotificationGroupsService) => {
    expect(service).toBeTruthy();
  }));
});
