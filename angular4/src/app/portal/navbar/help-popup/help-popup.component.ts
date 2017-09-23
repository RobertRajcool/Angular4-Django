import { Component, OnInit } from '@angular/core';

@Component({
    selector: 'app-help-popup',
    templateUrl: './help-popup.component.html',
    styleUrls: ['./help-popup.component.scss']
})
export class HelpPopupComponent implements OnInit {
    helpVideos: Array<{
        label: string;
        url: string;
    }> = [
        { label: 'How to place Microsoft Azure Order', url: 'https://www.youtube.com/embed/07dVPhSLG88' },
        { label: 'How to place Amazon Web Services Order', url: 'https://www.youtube.com/embed/sE0buvn63p0' },
        { label: 'How to place Vaultize/Freshdesk/Lifesize Orders', url: 'https://www.youtube.com/embed/5oK4BClxTVo' },
        { label: 'How to place Office 365 Order', url: 'https://www.youtube.com/embed/0GkCdSlPLlI' }
    ];

    constructor() { }

    ngOnInit() {
    }

}
