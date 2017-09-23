/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { NotificationActionsService } from './notification-actions.service';

describe('NotificationActionsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [NotificationActionsService]
    });
  });

  it('should ...', inject([NotificationActionsService], (service: NotificationActionsService) => {
    expect(service).toBeTruthy();
  }));
});
