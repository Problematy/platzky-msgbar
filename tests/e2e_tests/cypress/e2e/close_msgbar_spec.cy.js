describe('msgbar plugin behaviour', () => {
    beforeEach(() => {
        cy.visit('/');
    });
    
    it('should close the message bar when close button is clicked', () => {
        cy.get('#MsgBar', { timeout: 10000 }).should('be.visible')
        cy.get('#MsgBar .close-btn').click();
        cy.get('#MsgBar').should('not.exist');
        cy.get('#MsgBarStyle').should('not.exist');
    })
})