describe('msgbar plugin behaviour', () => {
    beforeEach(() => {
        cy.visit('/');
    });
    
    it('should close the message bar when close button is clicked', () => {
        cy.get('#MsgBar', { timeout: 10000 }).should('exist').and('be.visible')
        cy.get('#MsgBar .close-btn').should('be.visible').scrollIntoView().click();
        cy.get('#MsgBar').should('not.exist');
        cy.get('#MsgBarStyle').should('not.exist');
    })
})