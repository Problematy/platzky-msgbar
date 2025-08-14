describe('msgbar plugin behaviour', () => {
    beforeEach(() => {
        cy.visit('/');
    });
    
    it('should close the message bar when close button is clicked', () => {
        cy.get('#MsgBar', { timeout: 10000 }).should('exist').and('be.visible')
        cy.get('#MsgBar').then(($el) => {
            // Check computed styles
            const styles = window.getComputedStyle($el[0])
            console.log('MsgBar styles:', {
                display: styles.display,
                visibility: styles.visibility,
                opacity: styles.opacity,
                top: styles.top,
                left: styles.left
            })
            
            // Check if in viewport
            const rect = $el[0].getBoundingClientRect()
            console.log('Viewport position:', rect)
            })
            
        cy.get('#MsgBar .close-btn').click();
        cy.get('#MsgBar').should('not.exist');
        cy.get('#MsgBarStyle').should('not.exist');
    })
})