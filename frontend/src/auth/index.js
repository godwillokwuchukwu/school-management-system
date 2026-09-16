/**
 * Riverside Academy - Authentication & Portal Login Module
 *
 * Consolidates all login, registration, account activation,
 * and portal authentication interfaces in one unified module.
 */

export { default as StudentAuth } from './StudentAuth'
export { default as PortalLogin } from './PortalLogin'
export { default as AuthFlow } from './PortalLogin' // Backward compatibility alias
export { default as ParentRegister } from './ParentRegister'
export { default as ActivateAccount } from './ActivateAccount'
export { default as ActivateFlow } from './ActivateAccount' // Backward compatibility alias

import StudentAuth from './StudentAuth'
import PortalLogin from './PortalLogin'
import ParentRegister from './ParentRegister'
import ActivateAccount from './ActivateAccount'

const auth = {
  StudentAuth,
  PortalLogin,
  AuthFlow: PortalLogin,
  ParentRegister,
  ActivateAccount,
  ActivateFlow: ActivateAccount,
}

export default auth
